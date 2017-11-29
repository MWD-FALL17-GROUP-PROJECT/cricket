# -*- coding: utf-8 -*-

from computations import decompositions
from data import DataHandler
import pandas as pd
from collections import defaultdict
from operator import itemgetter
from util import constants
from util import formatter
import numpy as np
from computations import metrics
from computations import personalizedpagerank as ppr
from computations import LSH as lsh
from computations import rNearestNeighborSimilarMovies
from computations import relevanceFeedback
DataHandler.vectors()
global wt
import sklearn.metrics.pairwise as pairwise


def genre_spaceTags_LDA(genre):
    DataHandler.vectors()
    movie_tag_map,tag_id_map,actor_movie_rank_map,movie_actor_rank_map = DataHandler.get_dicts()
    df = DataHandler.load_genre_matrix(genre)
    ldaModel,doc_term_matrix,id_Term_map  =  decompositions.LDADecomposition(df,5,constants.genreTagsSpacePasses)
    topic_terms = defaultdict(set)
    for i in range(0,5):
        for tuples in ldaModel.get_topic_terms(i):#get_topics_terms returns top n(default = 10) words of the topics
            term = tag_id_map.get(id_Term_map.get(tuples[0]))
            topic_terms[i].add((term,tuples[1]))
    for i in range(0,5):
        print(sorted(topic_terms.get(i),key = itemgetter(1),reverse=True))
        print('\n')
    return

def genre_spaceActors_LDA(genre):
    movie_tag_map,tag_id_map,actor_movie_rank_map,movie_actor_rank_map = DataHandler.get_dicts()
    df = DataHandler.load_genre_actor_matrix(genre)
    ldaModel,doc_term_matrix,id_Term_map  =  decompositions.LDADecomposition(df,5,constants.genreActorSpacePasses)
    topic_terms = defaultdict(set)
    for i in range(0,5):
        for tuples in ldaModel.get_topic_terms(i):#get_topics_terms returns top n(default = 10) words of the topics
            term = id_Term_map.get(tuples[0])
            topic_terms[i].add((term,tuples[1]))
    for i in range(0,5):
        print(sorted(topic_terms.get(i),key = itemgetter(1),reverse=True))
        print('\n')

        
def top10_Actors_LDA(givenActor):
    DataHandler.create_actor_actorid_map()
    top10SimilarActors_similarity = DataHandler.similarActors_LDA(givenActor)
    print('Actors similar to '+str(DataHandler.actor_actorid_map[givenActor]))
    for actor,sim in top10SimilarActors_similarity:
        print(DataHandler.actor_actorid_map[actor]+' '+str(sim))

def prettyPrintVector(vector, actorsInDf, actorIdActorsDf, indexId):
    vectorLen = len(vector)
    for index in range(0, vectorLen):
        actorId = actorsInDf[index]
        actorName = actorIdActorsDf[actorIdActorsDf[indexId]==actorId].iloc[0][1]
        print(actorName + ": " + str(vector[index]), end=', ')
    print('.')
    
def prettyPrintYearVector(vector, actorsInDf, actorIdActorsDf, indexId):
    vectorLen = len(vector)
    for index in range(0, vectorLen):
        actorId = actorsInDf[index]
        actorName = actorIdActorsDf[actorIdActorsDf[indexId]==actorId].iloc[0][2]
        print(str(actorName) + ": " + str(vector[index]), end=', ')
    print('.')
    
def prettyPrintRankVector(vector, actorsInDf, actorIdActorsDf, indexId):
    vectorLen = len(vector)
    for index in range(0, vectorLen):
        actorId = actorsInDf[index]
        actorName = actorIdActorsDf[actorIdActorsDf[indexId]==actorId].iloc[0][3]
        print(str(actorName) + ": " + str(vector[index]), end=', ')
    print('.')
    
def top5LatentCP(tensorIdentifier, space):
    if (tensorIdentifier == 'AMY'):
        tensor, actors, movies, years = DataHandler.getTensor_ActorMovieYear()
        u = decompositions.CPDecomposition(tensor, constants.RANK)
        if (space == 'Actor'):
            actorIdActorsDf = DataHandler.actor_info_df
            actorRank = np.array(u[0])
            split_group_with_index = formatter.splitGroup(actorRank, 5)
            get_partition_on_ids(split_group_with_index, actorIdActorsDf['name'])
            semantics = np.matrix(actorRank.T).tolist()
            
            print("Top 5 semantics are:")
            for semantic in semantics:
                prettyPrintVector(semantic, actors, actorIdActorsDf, 'id')
                print("")
            
            return
        if (space == 'Movie'):
            movieIdMoviesDf = DataHandler.genre_movie_df
            movieRank = np.array(u[1])
            split_group_with_index = formatter.splitGroup(movieRank, 5)
            get_partition_on_ids(split_group_with_index, movieIdMoviesDf['moviename'])
            
            semantics = np.matrix(movieRank.T).tolist()
            
            print("Top 5 semantics are:")
            for semantic in semantics:
                prettyPrintVector(semantic, movies, movieIdMoviesDf, 'movieid')
                print("")
                
            return
        if (space == 'Year'):
            movieIdMoviesDf = DataHandler.genre_movie_df
            YearRank = np.array(u[2])
            split_group_with_index = formatter.splitGroup(YearRank, 5)
            get_partition_on_ids(split_group_with_index, years)
            
            semantics = np.matrix(YearRank.T).tolist()
            
            print("Top 5 semantics are:")
            for semantic in semantics:
                prettyPrintYearVector(semantic, years, movieIdMoviesDf, 'year')
                print("")
                
            return
        else:
            print('Wrong Space')
            return
    if (tensorIdentifier == 'TMR'):
        tensor, tags, movies, ranks = DataHandler.getTensor_TagMovieRating()
        u = decompositions.CPDecomposition(tensor,constants.RANK)
        if (space == 'Tag'):
            tagIdTagsDf = DataHandler.tag_id_df
            tagRank = np.array(u[0])
            split_group_with_index = formatter.splitGroup(tagRank, 5)
            get_partition_on_ids(split_group_with_index, tagIdTagsDf['tag'])
            semantics = np.matrix(tagRank.T).tolist()
            
            print("Top 5 semantics are:")
            for semantic in semantics:
                prettyPrintVector(semantic, tags, tagIdTagsDf, 'tagId')
                print("")
                
            return
        if (space == 'Movie'):
            movieIdMoviesDf = DataHandler.genre_movie_df
            movieRank = np.array(u[1])
            split_group_with_index = formatter.splitGroup(movieRank, 5)
            get_partition_on_ids(split_group_with_index, movieIdMoviesDf['moviename'])
            semantics = np.matrix(movieRank.T).tolist()
            
            print("Top 5 semantics are:")
            for semantic in semantics:
                prettyPrintVector(semantic, movies, movieIdMoviesDf, 'movieid')
                print("")
                
            return
        if (space == 'Rating'):
            userRatings = DataHandler.user_ratings_df
            RankingRank = np.array(u[2])
            split_group_with_index = formatter.splitGroup(RankingRank, 5)
            get_partition_on_ids(split_group_with_index, ranks)
            semantics = np.matrix(RankingRank.T).tolist()
            
            print("Top 5 semantics are:")
            for semantic in semantics:
                prettyPrintRankVector(semantic, ranks, userRatings, 'rating')
                print("")
                
            return
        else:
            print('Wrong Space')
            return
    else:
        print('Wrong Tensor Identifier')

data_required = {}

def get_partition_on_ids(split_group_with_index, data) :
    data_required.clear()
    for i in range(len(split_group_with_index)):
      for j in range(len(split_group_with_index[i])):
         if i in data_required :
             data_required.get(i).append(data[split_group_with_index[i][j]])
         else :
             data_required.update({i : [data[split_group_with_index[i][j]]]})
    
    return data_required
    
def get_partition_subtasks() :
    for x, v in data_required.items() :
        print ('Group ' + str(x+1) + ' : ' + str(v))
        print (" ")
    #print(data_required)
        
#def PPR_top10_SimilarActors(seed):
#    DataHandler.createDictionaries1()
#    DataHandler.create_actor_actorid_map()
#    actact = DataHandler.actor_actor_similarity_matrix()
#    actor_actorid_map = DataHandler.actor_actorid_map
#    alpha = constants.ALPHA
#    act_similarities = pagerank.PPR(actact,seed,alpha)
#    print('Top 10 actors similar to the following seed actors: '+str([actor_actorid_map.get(i) for i in seed]))
#    for index,sim in act_similarities:
#        print(actor_actorid_map.get(actact.columns[index])+' '+ str(sim))
#        
#def PPR_top10_SimilarCoActors(seed):
#    DataHandler.createDictionaries1()
#    DataHandler.create_actor_actorid_map()
#    actact = DataHandler.actor_actor_similarity_matrix()
#    actor_actorid_map = DataHandler.actor_actorid_map
#    alpha = constants.ALPHA
#    act_similarities = pagerank.PPR(actact,seed,alpha)
#    print('Co Actors similar to the following seed actors: '+str([actor_actorid_map.get(i) for i in seed]))
#    for index,sim in act_similarities:
#        print(actor_actorid_map.get(actact.columns[index])+' '+ str(sim))
#
##userMovies = user_rated_or_tagged_map.get(67348)
#def top5SimilarMovies(userMovies):
#    DataHandler.createDictionaries1()
#    u = decompositions.CPDecomposition(DataHandler.getTensor_ActorMovieGenreYear(),5)
#    movies = sorted(list(DataHandler.movie_actor_map.keys()))
#    u1= u[1]
#    movieNewDSpace = pd.DataFrame(u1,index = movies)
#    movie_movie_similarity = DataHandler.movie_movie_Similarity(movieNewDSpace)
#    movieid_name_map = DataHandler.movieid_name_map
#    alpha = constants.ALPHA
#    movie_similarities = pagerank.PPR(movie_movie_similarity,userMovies,alpha)
#    print('Movies similar to the following seed movies: '+str([movieid_name_map.get(i) for i in userMovies]))
#    for index,sim in movie_similarities:
#        if (movie_movie_similarity.columns[index] not in userMovies):
#            print(movieid_name_map.get(movie_movie_similarity.columns[index])+' '+ str(sim))

	
def PersnalizedPageRank_top10_SimilarActors(seed):
    DataHandler.createDictionaries1()
    DataHandler.create_actor_actorid_map()
    actact = DataHandler.actor_actor_invSimilarity_matrix()
    actor_actorid_map = DataHandler.actor_actorid_map
    alpha = constants.ALPHA
    act_similarities = ppr.personalizedPageRank(actact,seed,alpha)
    actors = list(actact.index)
    actorDF = pd.DataFrame(pd.Series(actors),columns = ['Actor'])
    actorDF['Actor'] = actorDF['Actor'].map(lambda x:actor_actorid_map.get(x))
    Result = pd.concat([act_similarities,actorDF],axis = 1)
    sortedResult=Result.sort_values(by=0,ascending=False).head(15)
    seedAcotorNames = [actor_actorid_map.get(i) for i in seed]
    print('Actors similar to the following seed actors: '+str(seedAcotorNames))
    for index in sortedResult.index:
        if sortedResult.loc[index,'Actor'] not in seedAcotorNames:
            print(sortedResult.loc[index,'Actor']+' '+ str(sortedResult.loc[index,0]))
        
def PersnalizedPageRank_top10_SimilarCoActors(seed):
    DataHandler.createDictionaries1()
    DataHandler.create_actor_actorid_map()
    coactcoact, ignoreVariable = DataHandler.coactor_siilarity_matrix()
    actor_actorid_map = DataHandler.actor_actorid_map
    alpha = constants.ALPHA
    act_similarities = ppr.personalizedPageRank(coactcoact,seed,alpha)
    actors = list(coactcoact.index)
    actorDF = pd.DataFrame(pd.Series(actors),columns = ['Actor'])
    actorDF['Actor'] = actorDF['Actor'].map(lambda x:actor_actorid_map.get(x))
    Result = pd.concat([act_similarities,actorDF],axis = 1)
    sortedResult=Result.sort_values(by=0,ascending=False).head(15)
    seedAcotorNames = [actor_actorid_map.get(i) for i in seed]
    print('Co Actors similar to the following seed actors: '+str(seedAcotorNames))
    for index in sortedResult.index:
        if sortedResult.loc[index,'Actor'] not in seedAcotorNames:
            print(sortedResult.loc[index,'Actor']+' '+ str(sortedResult.loc[index,0]))

#userMovies = user_rated_or_tagged_map.get(67348)
#userMovies = user_rated_or_tagged_map.get(3)
def PersnalizedPageRank_top5SimilarMovies(userMovies):
    DataHandler.createDictionaries1()
    u = decompositions.CPDecomposition(DataHandler.getTensor_ActorMovieGenreYearRankRating(),5)
    movies = sorted(list(DataHandler.movie_actor_map.keys()))
    u1= u[1]
    movieNewDSpace = pd.DataFrame(u1,index = movies)
    movie_movie_similarity = DataHandler.movie_movie_Similarity(movieNewDSpace)
    movieid_name_map = DataHandler.movieid_name_map
    alpha = constants.ALPHA
    movie_similarities = ppr.personalizedPageRank(movie_movie_similarity,userMovies,alpha)
    movies = list(movie_movie_similarity.index)
    movieDF = pd.DataFrame(pd.Series(movies),columns = ['movies'])
    movieDF['movies'] = movieDF['movies'].map(lambda x:movieid_name_map.get(x))
    Result = pd.concat([movie_similarities,movieDF],axis = 1)
    sortedResult=Result.sort_values(by=0,ascending=False).head(15)
    seedmovieNames = [movieid_name_map.get(i) for i in userMovies]
    print('Movies similar to the following seed movies: '+str(seedmovieNames))
    movie_genre_map = DataHandler.movie_genre_map
    genreForSeedMovies = [movie_genre_map.get(i) for i in userMovies]    
    print('Genres for seed movies: '+str(genreForSeedMovies))
    for index in sortedResult.index:
        if sortedResult.loc[index,'movies'] not in seedmovieNames:
            print(sortedResult.loc[index,'movies']+' '+ str(sortedResult.loc[index,0])+' '+str(movie_genre_map.get(movies[index])))


def top5SimilarMovies1(userMovies):
    DataHandler.createDictionaries1()
    u = decompositions.CPDecomposition(DataHandler.getTensor_ActorMovieGenreYearRankRating(),5)
    movies = sorted(list(DataHandler.movie_actor_map.keys()))
    u1= u[1]
    movieNewDSpace = pd.DataFrame(u1,index = movies)
    movie_movie_similarity = DataHandler.movie_movie_Similarity1(movieNewDSpace)
    movieid_name_map = DataHandler.movieid_name_map
    alpha = constants.ALPHA
    movie_similarities = pagerank.PPR(movie_movie_similarity,userMovies,alpha)
    print('Movies similar to the following seed movies: '+str([movieid_name_map.get(i) for i in userMovies]))
    for index,sim in movie_similarities:
        if (movie_movie_similarity.columns[index] not in userMovies):
            print(movieid_name_map.get(movie_movie_similarity.columns[index])+' '+ str(sim))

            
def PersnalizedPageRank_top5SimilarMovies1(userMovies):
    DataHandler.createDictionaries1()
    u = decompositions.CPDecomposition(DataHandler.getTensor_ActorMovieGenreYearRankRating(),5)
    movies = sorted(list(DataHandler.movie_actor_map.keys()))
    u1= u[1]
    movieNewDSpace = pd.DataFrame(u1,index = movies)
    movie_movie_similarity = DataHandler.movie_movie_Similarity1(movieNewDSpace)
    movieid_name_map = DataHandler.movieid_name_map
    alpha = constants.ALPHA
    movie_similarities = ppr.personalizedPageRank(movie_movie_similarity,userMovies,alpha)
    movies = list(movie_movie_similarity.index)
    movieDF = pd.DataFrame(pd.Series(movies),columns = ['movies'])
    movieDF['movies'] = movieDF['movies'].map(lambda x:movieid_name_map.get(x))
    Result = pd.concat([movie_similarities,movieDF],axis = 1)
    sortedResult=Result.sort_values(by=0,ascending=False).head(15)
    seedmovieNames = [movieid_name_map.get(i) for i in userMovies]
    print('Movies similar to the following seed movies: '+str(seedmovieNames))
    movie_genre_map = DataHandler.movie_genre_map
    genreForSeedMovies = [movie_genre_map.get(i) for i in userMovies]    
    print('Genres for seed movies: '+str(genreForSeedMovies))
    for index in sortedResult.index:
        if sortedResult.loc[index,'movies'] not in seedmovieNames:
            print(sortedResult.loc[index,'movies']+' '+ str(sortedResult.loc[index,0])+' '+str(movie_genre_map.get(movies[index])))

def Recommender(userId):
    DataHandler.createDictionaries1()
    movieRatedSeed = DataHandler.userMovieRatings(userId)
    
    
    actor_movie_rank_map = DataHandler.actor_movie_rank_map
    decomposed = decompositions.CPDecomposition(DataHandler.getTensor_ActorMovieGenre(),5)
    moviesList = sorted(list(DataHandler.movie_actor_rank_map.keys()))
    movie_movie_similarity = DataHandler.movie_movie_Similarity1(pd.DataFrame(decomposed[1],index=moviesList))
    prData = ppr.personalizedPageRankWeighted(movie_movie_similarity, movieRatedSeed, 0.9)
    rankedItems = sorted(list(map(lambda x:(moviesList[x[0]],x[1]),prData.itertuples())),key=lambda x:x[1], reverse=True)
    movieid_name_map = DataHandler.movieid_name_map

    seedmovieNames = [movieid_name_map[k] for k,y in movieRatedSeed]
    print("Movies similar to the users seed movies " + str(seedmovieNames) + " are:")
    return [(movieid_name_map[k],y) for (k,y) in rankedItems if k not in [k for k,y in movieRatedSeed]]


def calcWeightedSimilarity(col):
    return sum(col*wt)/sum(wt)

"""
This Function takes a Movie Movie Similarity DataFrame and user id:
Returns sorted list of movies similar to the movies watched by the 
user based on the order in which the movies were watched.
"""
def getWeightedSimilarityOrder(similarity_df,userId):
    global wt
    moviesWatched = list(DataHandler.user_rated_or_tagged_map.get(userId))
    moviesList = sorted(list(DataHandler.movie_actor_rank_map.keys()))
    moviesWatched_timestamp = list(DataHandler.user_rated_or_tagged_date_map.get(userId))
    moviesWatched_timestamp = sorted(moviesWatched_timestamp,key=itemgetter(1))
    moviesWatched_timestamp_sorted = list(list(zip(*moviesWatched_timestamp ))[0])
    movie_movie_similarity_subset = similarity_df.loc[moviesWatched_timestamp_sorted][list(set(moviesList)-set(moviesWatched))]
    wt = list(range(1,len(movie_movie_similarity_subset)+1))
    weightedSimilarities = movie_movie_similarity_subset.apply(calcWeightedSimilarity,axis=0)
    return weightedSimilarities.sort_values(ascending=False).index[0:5], weightedSimilarities.sort_values(ascending=False)[0:5]

def task1a_PCA(userId):
    DataHandler.vectors()
    DataHandler.createDictionaries1()
    movie_tag_df=DataHandler.load_movie_tag_df()
    u = decompositions.PCADimensionReduction((movie_tag_df),5) #Assuming number of latent semantics are 5
    decpmposed=pd.DataFrame(u,index =movie_tag_df.index )
    similarity_df=DataHandler.movie_movie_Similarity1(decpmposed)
    movie_list=getWeightedSimilarityOrder(similarity_df,userId)
    
    user_movie_timestamp_map=DataHandler.user_rated_or_tagged_date_map
    list(DataHandler.user_rated_or_tagged_date_map[userId]).sort(key=lambda tup: tup[1])
    user_watched_movies={}
    #Code to get the movies the user has already watched
    for user, movies in user_movie_timestamp_map.items():
        for i in user_movie_timestamp_map[user]:
            if user not in user_watched_movies:
                user_watched_movies[user]=[i[0]]
            else:
                user_watched_movies[user].append(i[0])
                
    movieid_name_map = DataHandler.movieid_name_map
    print('Movies similar to the following seed movies: '+str([movieid_name_map.get(i) for i in user_watched_movies[userId]]))
    for i in range(0,len(movie_list[0])):
        print(movieid_name_map[movie_list[0][i]]+': '+ str(list(movie_list[1])[i]))    

def task1c(userId):
    global wt
    DataHandler.createDictionaries1()
    decomposed = decompositions.CPDecomposition(DataHandler.getTensor_ActorMovieGenre(),5)
    moviesList = sorted(list(DataHandler.movie_actor_rank_map.keys()))
    movie_movie_similarity = DataHandler.movie_movie_Similarity1(pd.DataFrame(decomposed[1],index=moviesList))
    
    moviesWatched_timestamp = list(DataHandler.user_rated_or_tagged_date_map.get(userId))
    
    moviesWatched_timestamp = sorted(moviesWatched_timestamp,key=itemgetter(1))
    moviesWatched_timestamp_sorted = list(list(zip(*moviesWatched_timestamp ))[0])
    resultMovies = getWeightedSimilarityOrder(movie_movie_similarity,userId)
    movieid_name_map = DataHandler.movieid_name_map
    resultMovieNames = [movieid_name_map[movieid] for movieid in resultMovies]
    watchedMovieNames = [movieid_name_map[movieid] for movieid in moviesWatched_timestamp_sorted]
    print('Movies Watched by the user in order: '+ str(watchedMovieNames))
    print('Top 5 movies : '+ str(resultMovieNames))

def task3_MDS_SVD(iterations) :
    P = DataHandler.load_movie_tag_df() 
    
    X, Sigma, VT = decompositions.SVDDecomposition(P, 500);
    
    dissimilarities = pairwise.euclidean_distances(P)
   # movieList = dissimilarities.index
    #dissimilarities=np.matrix(dissimilarities)
    
     dissimilarities = pairwise.euclidean_distances(P)
    
    
    
    #A = pd.DataFrame(U, index = P.index)
    
    #A.to_csv('foo.csv')
    
    #dissimilarities = np.matrix(U) * np.matrix(U.T)
    #movieList = dissimilarities.index
    #dissimilarities=np.matrix(dissimilarities)
    
    
    dis = pairwise.euclidean_distances(U)
        
        # Compute stress
    stress = np.square((dis.ravel() - dissimilarities.ravel())).sum() / 2
        
        
def task3():
    #3.1
    DataHandler.createDictionaries1()
    movieid_name_map = DataHandler.movieid_name_map
    MoviesinLatentSpace = pd.read_csv(constants.DIRECTORY+'MoviesinLatentSpace_SVD_MDS.csv',index_col = 0)
    MoviesinLatentSpace_Matrix = np.matrix(MoviesinLatentSpace,dtype = np.float32)
    print("Mapped all the movies to 500 dimensional space\n")
    d = len(MoviesinLatentSpace.columns)
    w = constants.W
    MoviesinLatentSpace_Matrix = np.matrix(MoviesinLatentSpace,dtype = np.float32)
    
    indexing = True
    while indexing:
        L = input("Please enter the number of Layers 'L': ")
        if not L.isdigit():
            print("A Non Integer was given as input. L should be an integer.\n")
            indexing = True
            continue
        else:
            L = int(L)
        k = input("Please enter the number of hashes per layer 'k': ")
        if not k.isdigit():
            print("A Non Integer was given as input. k should be an integer.\n")
            indexing = True
            continue
        else:
            k = int(k)
        #layerTables stores L*K random 'd' dimensional vectors and random offset values 'b'
        #LHashTables_result constains hashtables for each layer with keys provided by it's K hash functions and values as the movie indices
        layerTables,LHashTables_result = lsh.createAndGetLSH_IndexStructure(L,k,d,w,MoviesinLatentSpace_Matrix)
        print("Index Structure Created\n")
        indexing = False
    
    reIndex = False
    doSearch = False
    exitVar = False
    takeUserInput = True
    while not exitVar :
        wantFeedback = True
        
        if takeUserInput:
            print("To Re-Index the index structure Press 'R'")
            print("To perform rNearestNeigbhor Search Press 'S'")
            print("To Exit Press 'X'")
            userInput = input("Your Response: ")
            if userInput == 'X':
                print("Exiting..")
                break
            elif userInput == "R":
                print("Re-Indexing..")
                reIndex = True
            elif userInput == "S":
                doSearch = True
            else:
                print("Invalid input. Please choose among the following: \n")
                takeUserInput = True
                continue
        
        if reIndex:
            reIndex = True
            while reIndex:
                L = input("Please enter the number of Layers 'L': ")
                if not L.isdigit():
                    print("A Non Integer was given as input. L should be an integer. Please try again\n")
                    reIndex = True
                    continue
                else:
                    L = int(L)
                k = input("Please enter the number of hashes per layer 'k': ")
                if not k.isdigit():
                    print("A Non Integer was given as input. k should be an integer. Please try again\n")
                    reIndex = True
                    continue
                else:
                    k = int(k)
                    reIndex = False
            layerTables,LHashTables_result = lsh.createAndGetLSH_IndexStructure(L,k,d,w,MoviesinLatentSpace_Matrix)
            print("Index Structure Created Again\n")
            reIndex = False
        if doSearch:
            doSearch = True
            while doSearch:
                movieid = input("Please enter a movieID: ")
                if not movieid.isdigit():
                    print("A Non Integer was given as input. movieid should be an integer. Please try again\n")
                    doSearch = True
#                    takeUserInput = False
#                    reIndex = False
                    continue
                else:
                    movieid = int(movieid)
                    doSearch = False
                if movieid not in MoviesinLatentSpace.index:
                    print("The given movieid does not exist. Please try again\n")
                    doSearch = True
#                    takeUserInput = False
#                    reIndex = False
                    continue
                r = input("Please enter the number of nearest neighbors 'r': ")
                if not r.isdigit():
                    print("A Non Integer was given as input. r should be a non zero positive integer. Please try again\n")
                    doSearch = True
#                    takeUserInput = False
#                    reIndex = False
                    continue
                else:
                    r = int(r)
                    doSearch = False
                if r == 0:
                    print("0 was given as input. r should be a non zero positive integer. Please try again\n")
                    doSearch = True
                    takeUserInput = False
                    reIndex = False
                    continue
            moviePoint = MoviesinLatentSpace_Matrix[list(MoviesinLatentSpace.index).index(movieid)].astype(np.float32)
            nearestMovies,nearestMoviesBruteForce,nearestMoviesDistance,nearestMoviesDistanceBruteForce = rNearestNeighborSimilarMovies.getRNearestNeighbors(movieid,moviePoint,r,MoviesinLatentSpace,layerTables,LHashTables_result)
            nearestMoviesDistance,nearestMoviesDistanceBruteForce = list(np.array(nearestMoviesDistance)[0])[:r],list(np.array(nearestMoviesDistanceBruteForce)[0])[:r]
            if len(nearestMovies) == 0:
                print("The LSH based index structure didn't map any other movie in the same buckets.\n")
                continue
            if len(nearestMovies) != r:
                print("The LSH based index structure didn't map enough movies in the same buckets.\n")
            nearestMoviesNames = [movieid_name_map[mid] for mid in nearestMovies]
            nearestMoviesBruteForceNames = [movieid_name_map[mid] for mid in nearestMoviesBruteForce]
            print("Movies Similar to '"+str(movieid_name_map[movieid])+"'\n")
            print("Results based on the LSH based rNearestNeighbors and their distance scores: \n"+str(list(zip(nearestMoviesNames,nearestMoviesDistance)))+"\n")
            print("Results based on Brute Force rNearestNeighbors and their distance scores: \n"+str(list(zip(nearestMoviesBruteForceNames,nearestMoviesDistanceBruteForce)))+"\n")
            while wantFeedback:
                feedback = input("Would you like to give feedback 'Y'/'N': ")
                if feedback == 'Y':
                    task4(moviePoint, r, movieid, LHashTables_result, MoviesinLatentSpace, layerTables, nearestMovies)
                    wantFeedback = True
                elif feedback == 'N':
                    wantFeedback = False
                else:
                    print("Invalid Input provided. Please try again.")
                    wantFeedback = True
            takeUserInput = True
                    
    
    
def task4(moviePoint, r, movieid, LHashTables_result, MoviesinLatentSpace, layerTables, nearestMovies) :
    movieid_name_map = DataHandler.movieid_name_map
    takeFeedback = True
    while takeFeedback:
        feedback = input("Relevance (1/0) for each of the "+ str(r) +" movies: ")
        feedback_split = feedback.split(',')
        if len(feedback_split) != len(nearestMovies):
            print("Invalid Feedback string. Please give feedback for each of the movies.\n")
            takeFeedback = True
            continue
        elif any(isinstance(x, int) for x in feedback_split):
            print("Invalid Feedback string.\n")
            takeFeedback = True
            continue
        else:
            feedback = np.array([int(i) for i in feedback_split])
            if not ((feedback<= 1 ).sum() == feedback.size):
                print("Invalid Feedback string.\n")
                takeFeedback = True
            elif not ((feedback>= 0 ).sum() == feedback.size):
                print("Invalid Feedback string.\n")
                takeFeedback = True
                continue
            else:
                takeFeedback = False
    
    relevantFeedback = np.where(feedback == 1)[0]
    irrelevantFeedback = np.where(feedback == 0)[0]
    
    relevantMovieList = [nearestMovies[i] for i in relevantFeedback]
    irrevelantMovieList = [nearestMovies[i] for i in irrelevantFeedback]
    takeUserInput = True
    while takeUserInput:
        print("For LDE Dec-Hi Press 'LH'")
        print("For LDE Regular Press 'LR'")
        print("For Standard Rochio Press 'R'")
        userInput = input("Your Response: ")
        if userInput == 'LH':
           newMoviePoint = relevanceFeedback.newQueryFromLDEDecHiFeedBack(moviePoint, relevantMovieList, irrevelantMovieList, nearestMovies, MoviesinLatentSpace)
           takeUserInput = False
        elif userInput == "LR":
           newMoviePoint = relevanceFeedback.newQueryFromLDERegularFeedBack(moviePoint, relevantMovieList, irrevelantMovieList, nearestMovies, MoviesinLatentSpace) 
           takeUserInput = False
        elif userInput == "R":
            newMoviePoint = relevanceFeedback.newQueryFromRochioFeedBack(moviePoint, relevantMovieList, irrevelantMovieList, MoviesinLatentSpace)
            takeUserInput = False
        else:
            print("Invalid input. Please choose among the following: \n")
            takeUserInput = True
            continue
    nearestMovies1,nearestMoviesBruteForce1,nearestMoviesDistance,nearestMoviesDistanceBruteForce = rNearestNeighborSimilarMovies.getRNearestNeighbors(movieid,newMoviePoint,r,MoviesinLatentSpace,layerTables,LHashTables_result)
    nearestMoviesDistance,nearestMoviesDistanceBruteForce = list(np.array(nearestMoviesDistance)[0])[:r],list(np.array(nearestMoviesDistanceBruteForce)[0])[:r]
    nearestMoviesNames1 = [movieid_name_map[mid] for mid in nearestMovies1]
    nearestMoviesBruteForceNames1 = [movieid_name_map[mid] for mid in nearestMoviesBruteForce1]
    print("Movies Similar to "+str(movieid_name_map[movieid])+"\n")
    print("Results based on the LSH based rNearestNeighbors and their distance scores: \n"+str(list(zip(nearestMoviesNames1,nearestMoviesDistance)))+"\n")
    print("Results based on Brute Force rNearestNeighbors and their distance scores: \n"+str(list(zip(nearestMoviesBruteForceNames1,nearestMoviesDistanceBruteForce)))+"\n")
            

